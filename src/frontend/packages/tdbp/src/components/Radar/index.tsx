import React, { useEffect, useMemo, useState } from "react";

import ReactECharts from "echarts-for-react";
import cloneDeep from "lodash.clonedeep";
import { Select } from "@openfun/cunningham-react";
import { Card } from "@openfun/warren-core";
import { useIsFetching } from "@tanstack/react-query";
import { useSlidingWindow, Action, Resource } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";
import { Scores, useScore } from "../../api/getScores";
import { isInEnum } from "../ActiveActions/index";
import { RadarChartOption } from "../../types/chartOptions";

const baseOption: RadarChartOption = {
  tooltip: {
    trigger: "item",
    valueFormatter: (value) => value.toFixed(2),
    axisPointer: {
      // Use axis to trigger tooltip
      type: "shadow", // 'shadow' as default; can also be 'line' or 'shadow'
    },
  },
  legend: {
    data: ["Moyenne de la cohorte", "Score de l'étudiant"],
  },
  radar: {
    indicator: [],
  },
  series: [],
};

interface RadarProps {
  course_id: string;
}

/**
 * A React component for displaying a radar chart for students scores compared to the
 * cohort. This component displays, for each resources and activities, the average
 * scores of selected student along with the mean scores of the cohort.
 *
 * @returns {JSX.Element} The JSX for the Radar component.
 */
export const Radar = ({ course_id }: RadarProps) => {
  const { until } = useTdbpFilters();
  const { slidingWindow } = useSlidingWindow({ course_id, until });
  const { data } = useScore(
    { course_id, until, average: true },
    !!slidingWindow,
  );

  const [selectedStudent, setSelectedStudent] = useState<string>();

  const handleStudentChange = (
    value: string | string[] | number | undefined,
  ): void => {
    if (typeof value !== "string") {
      return;
    }
    setSelectedStudent(value);
  };

  const parseIndicators = (actions: Array<Action>) => {
    return actions.map((action) => ({ name: action.name, max: 100 }));
  };

  const parseSeries = (
    scores: Scores | undefined,
    student: string | undefined,
  ) => {
    const series = [];

    if (!scores?.average) {
      return [];
    }
    const cohortMeanScores = scores.average;
    series.push({
      name: "Moyenne de la cohorte",
      type: "radar",
      data: [
        {
          value: cohortMeanScores
            .map((score) => (score < 0 ? 0 : score))
            .map((score) => score * 100),
          name: "moyenne cohorte",
        },
      ],
    });

    if (!student || !scores?.scores) {
      return series;
    }
    const selectedStudentScores = scores.scores[student]
      .map((score: number) => (score < 0 ? 0 : score))
      .map((score: number) => score * 100);

    series.push({
      name: "Score de l'étudiant",
      type: "radar",
      data: [
        {
          value: selectedStudentScores,
          name: student,
        },
      ],
    });
    return series;
  };

  const studentOptions = useMemo(() => {
    if (!data?.scores) {
      return [];
    }
    return Object.keys(data?.scores).map((student) => ({
      value: student,
      label: student,
    }));
  }, [data]);

  const formattedOption = useMemo(() => {
    if (!slidingWindow?.active_actions) {
      return baseOption;
    }

    const activeActions = slidingWindow.active_actions;

    if (!activeActions.length) {
      return baseOption;
    }
    const newOption = cloneDeep(baseOption);
    // We assume all requests share the same xAxis.

    newOption.radar.indicator = parseIndicators(
      activeActions.filter((action) => isInEnum(action.module_type, Resource)),
    );
    newOption.series = parseSeries(data, selectedStudent);
    return newOption;
  }, [slidingWindow, data, selectedStudent]);

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
    <Card className="c__radar">
      <div className="c__radar__title">Scores étudiants</div>
      <Select
        label="Étudiant"
        defaultValue={selectedStudent}
        disabled={!data?.scores}
        options={studentOptions}
        multi={false}
        onChange={(selectedValue) =>
          handleStudentChange(selectedValue.target.value)
        }
      />
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
