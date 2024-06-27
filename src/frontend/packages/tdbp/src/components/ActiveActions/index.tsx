import { useEffect, useMemo, useState } from "react";

import ReactECharts from "echarts-for-react";
import cloneDeep from "lodash.clonedeep";
import dayjs from "dayjs";
import { Card, useLTIContext } from "@openfun/warren-core";
import { useIsFetching } from "@tanstack/react-query";
import {
  useSlidingWindow,
  Action,
  Activity,
  Resource,
} from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";
import { BarChartOption } from "../../types/chartOptions";

// Define a generic type for enum
export function isInEnum<T>(value: string, enumObject: T): boolean {
  // Check if the enum object is valid
  if (typeof enumObject !== "object" || enumObject === null) {
    throw new Error("Invalid enum object");
  }

  return Object.values(enumObject).includes(value);
}

const baseOption: BarChartOption = {
  tooltip: {
    trigger: "axis",
    axisPointer: {
      // Use axis to trigger tooltip
      type: "shadow", // 'shadow' as default; can also be 'line' or 'shadow'
    },
  },
  legend: {},
  grid: {
    left: "3%",
    right: "4%",
    bottom: "3%",
    containLabel: true,
  },
  xAxis: {
    type: "value",
    min: 0,
    max: 100,
  },
  yAxis: {
    type: "category",
    data: [],
  },
  series: [],
};

interface ActiveActionsProps {
  course_id: string;
  enumType: "Resource" | "Activity";
  title: string;
}

/**
 * A React functional component for displaying a stack horizontal bar chart of the
 * consultation rate of each resources and activities.
 *
 * @returns {JSX.Element} The JSX for the Activites component.
 */
export const ActiveActions = ({
  course_id,
  enumType,
  title,
}: ActiveActionsProps) => {
  const { until } = useTdbpFilters();
  const { appData } = useLTIContext();
  const { slidingWindow } = useSlidingWindow({ course_id, until });

  const resources = useMemo(() => {
    if (!slidingWindow?.active_actions) {
      return [];
    }

    const activeActions = slidingWindow?.active_actions;

    if (!activeActions.length) {
      return [];
    }

    const enumTypeToUse = enumType === "Resource" ? Resource : Activity;

    const sortedResources = activeActions
      ?.filter((action) => isInEnum(action.module_type, enumTypeToUse))
      .sort((a, b) => a.activation_rate - b.activation_rate);
    return sortedResources;
  }, [slidingWindow]);

  const parseYAxis = (actions: Array<Action>): Array<string> =>
    actions.map((action) => action.name) || [];

  const parseSeries = (actions: Array<Action>) => {
    const series = [];

    if (appData.is_instructor) {
      series.push({
        name: "Score d'activation",
        type: "bar",
        stack: "total",
        label: {
          show: true,
          position: "insideLeft",
          formatter: (d: { dataIndex: number }) =>
            dayjs(actions[d.dataIndex].activation_date).format("DD/MM/YY"),
        },
        emphasis: {
          focus: "series",
        },
        data: actions.map((action) => ({
          value: action.activation_rate * 100,
        })),
      });
    } else {
      series.push({
        name: "Score d'activation",
        type: "bar",
        stack: "total",
        label: {
          show: true,
          position: "insideLeft",
          formatter: (d: { dataIndex: number }) =>
            dayjs(actions[d.dataIndex].activation_date).format("DD/MM/YY"),
        },
        emphasis: {
          focus: "series",
        },
        data: actions.map((action) => ({
          value: action.activation_rate * 100,
          itemStyle: {
            color: !action.is_activator_student ? undefined : "#a90000",
          },
        })),
      });
    }
    return series;
  };

  const formattedOption = useMemo(() => {
    if (!resources.length) {
      return baseOption;
    }
    const newOption = cloneDeep(baseOption);

    newOption.yAxis.data = parseYAxis(resources);

    newOption.series = parseSeries(resources);

    return newOption;
  }, [resources]);

  const currentFetchCount = useIsFetching();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (currentFetchCount > 0 && formattedOption.series.length === 0) {
      setIsLoading(true);
    } else {
      setIsLoading(false);
    }
  }, [currentFetchCount, formattedOption]);
  return (
    <Card className="c__activeactions">
      <div className="c__activeactions__title">{title}</div>
      <ReactECharts
        option={formattedOption}
        notMerge={false}
        showLoading={isLoading}
        loadingOption={{ text: "Chargement" }}
        style={{ height: 500, width: "100%" }}
      />
    </Card>
  );
};
