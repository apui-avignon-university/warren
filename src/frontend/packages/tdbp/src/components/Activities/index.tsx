import { useEffect, useMemo, useState } from "react";

import ReactECharts from "echarts-for-react";
import cloneDeep from "lodash.clonedeep";
import dayjs from "dayjs";
import { Card } from "@openfun/warren-core";
import { useIsFetching } from "@tanstack/react-query";
import { useSlidingWindow, Action, Resource } from "../../api/getSlidingWindow";
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

interface ActivitiesProps {
  course_id: string;
}

/**
 * A React functional component for displaying a stack horizontal bar chart of the
 * consultation rate of each resources and activities.
 *
 * @returns {JSX.Element} The JSX for the Activites component.
 */
export const Activities = ({ course_id }: ActivitiesProps) => {
  const { until } = useTdbpFilters();
  const { slidingWindow } = useSlidingWindow({ course_id, until });

  const resources = useMemo(() => {
    if (!slidingWindow?.active_actions) {
      return [];
    }

    const activeActions = slidingWindow?.active_actions;

    if (!activeActions.length) {
      return [];
    }
    const sortedResources = activeActions
      ?.filter((action) => isInEnum(action.module_type, Resource))
      .sort((a, b) => a.activation_rate - b.activation_rate);
    return sortedResources;
  }, [slidingWindow]);

  const parseYAxis = (actions: Array<Action>): Array<string> =>
    actions.map((action) => action.name) || [];

  const parseSeries = (actions: Array<Action>) => ({
    name: "Taux de consultation",
    type: "bar",
    stack: "total",
    label: {
      show: true,
      position: "insideLeft",
      formatter: (d: { dataIndex: number }) =>
        dayjs(actions[d.dataIndex].activation_date).format("DD/MM"),
    },
    emphasis: {
      focus: "series",
    },
    data: actions.map((action) => action.activation_rate * 100) || [],
  });

  const formattedOption = useMemo(() => {
    if (!resources.length) {
      return baseOption;
    }
    const newOption = cloneDeep(baseOption);

    newOption.yAxis.data = parseYAxis(resources);

    newOption.series = [parseSeries(resources)];

    return newOption;
  }, [resources]);

  const currentFetchCount = useIsFetching();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (currentFetchCount > 0 && formattedOption === baseOption) {
      setIsLoading(true);
    } else {
      setIsLoading(false);
    }
  }, [currentFetchCount, formattedOption]);
  return (
    <Card className="c__activities">
      <div className="c__activities__title">
        Taux de consultation des ressources
      </div>
      <ReactECharts
        option={formattedOption}
        notMerge={true}
        showLoading={isLoading}
        loadingOption={{ text: "Chargement" }}
        style={{ height: 500, width: "100%" }}
      />
    </Card>
  );
};
