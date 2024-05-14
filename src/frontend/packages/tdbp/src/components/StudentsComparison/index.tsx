import React, { useEffect, useMemo, useState } from "react";

import ReactECharts from "echarts-for-react";
import cloneDeep from "lodash.clonedeep";
import { Card } from "@openfun/warren-core";
import { useIsFetching } from "@tanstack/react-query";
import { Activity, Resource } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";
import { useScore } from "../../api/getScores";
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
  animation: false,
  legend: {},
  grid: {
    left: "3%",
    right: "4%",
    bottom: "3%",
    containLabel: true,
  },
  emphasis: {
    focus: "series",
    blurScope: "coordinateSystem",
  },
  dataZoom: [
    {
      type: "slider",
      yAxisIndex: 0,
      zoomLock: true,
      filterMode: "none",
      width: 10,
      right: 10,
      top: 70,
      bottom: 20,
      start: 95,
      end: 100,
      handleSize: 0,
      showDetail: false,
    },
    {
      type: "inside",
      yAxisIndex: 0,
      filterMode: "none",
      start: 95,
      end: 100,
      zoomOnMouseWheel: false,
      moveOnMouseMove: true,
      moveOnMouseWheel: true,
    },
  ],
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

interface StudentScore {
  username: string;
  scoreActivity: number;
  scoreResource: number;
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

  const sumScores = (scores: Array<number>, actionMask: Array<boolean>) => {
    const sum = scores
      .filter((_, idx) => actionMask[idx])
      .reduce((a, b) => a + b, 0);

    return sum < 0 ? 0 : sum;
  };

  const parseSerie = (serie: Array<number>, name: string) => {
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
      data: serie,
    };
  };

  const formattedOption = useMemo(() => {
    if (!data) {
      return baseOption;
    }

    const newOption = cloneDeep(baseOption);

    const studentScores: Array<StudentScore> = Object.entries(data.scores)
      .map(([username, scores]) => ({
        username,
        scoreActivity: sumScores(
          scores,
          data.actions.map((action) => isInEnum(action.module_type, Activity)),
        ),
        scoreResource: sumScores(
          scores,
          data.actions.map((action) => isInEnum(action.module_type, Resource)),
        ),
      }))
      .sort(
        (a, b) =>
          a.scoreActivity +
          a.scoreResource -
          (b.scoreActivity + b.scoreResource),
      );

    newOption.yAxis.data = studentScores.map((e) => e.username);

    newOption.series = [
      parseSerie(
        studentScores.map((e) => e.scoreResource),
        "Score ressource",
      ),
      parseSerie(
        studentScores.map((e) => e.scoreActivity),
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
