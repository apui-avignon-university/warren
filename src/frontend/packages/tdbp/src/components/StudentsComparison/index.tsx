import React, { useEffect, useMemo, useState } from "react";

import ReactECharts from "echarts-for-react";
import cloneDeep from "lodash.clonedeep";
import { Card } from "@openfun/warren-core";
import { useIsFetching } from "@tanstack/react-query";
import { Activity, Resource } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";
import { Scores, useScore } from "../../api/getScores";
import { isInEnum } from "../Activities";
import { BarChartOption } from "../../types/chartOptions";

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
  },
  yAxis: {
    type: "category",
    data: [],
  },
  series: [],
};

interface StudentsComparisonProps {
  course_id: string;
}

/**
 * A React component for displaying a stack horizontal bar chart of each student score
 * for resources and activies.
 *
 * @returns {JSX.Element} The JSX for the StudentsComparison component.
 */
export const StudentsComparison = ({ course_id }: StudentsComparisonProps) => {
  const { until } = useTdbpFilters();
  const { data } = useScore({ course_id, until, average: true });

  const parseSeries = (
    scores: Scores,
    actionMask: Array<boolean>,
    name: string,
  ) => {
    const studentsScore = Object.values(scores.scores).map((studentScores) => {
      const score = studentScores
        .filter((_, idx) => actionMask[idx])
        .reduce((a, b) => a + b, 0);

      return score < 0 ? 0 : score;
    });

    return {
      name,
      type: "bar",
      stack: "total",
      label: {
        show: true,
      },
      emphasis: {
        focus: "series",
      },
      data: studentsScore,
    };
  };

  const formattedOption = useMemo(() => {
    if (!data) {
      return baseOption;
    }

    const newOption = cloneDeep(baseOption);

    newOption.yAxis.data = Object.keys(data.scores);

    newOption.series = [
      parseSeries(
        data,
        data.actions.map((action) => isInEnum(action.module_type, Resource)),
        "Score ressource",
      ),
      parseSeries(
        data,
        data.actions.map((action) => isInEnum(action.module_type, Activity)),
        "Score activité",
      ),
    ];

    return newOption;
  }, [data]);

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
    <Card className="c__studentscomparison">
      <div className="c__studentscomparison__title">
        Scores cumulés pour toutes les actions
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
