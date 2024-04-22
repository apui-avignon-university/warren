import React from "react";

import dayjs from "dayjs";
import { Card } from "@openfun/warren-core";
import { useSlidingWindow } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";

interface WindowProps {
  course_id: string;
}

/**
 * A React component for displaying the sliding window date range computed.
 *
 * @returns {JSX.Element} The JSX for the Window component.
 */
export const Window = ({ course_id }: WindowProps) => {
  const { until } = useTdbpFilters();
  const { slidingWindow } = useSlidingWindow({ course_id, until });

  const formatter = (date: string) => dayjs(date).format("DD MMM YYYY");

  const content = !slidingWindow?.window
    ? "-"
    : [slidingWindow.window.since, slidingWindow.window.until]
        .map(formatter)
        .join(" - ");

  return (
    <Card className="c__window">
      <div className="c__window__title">Fenêtre flottante</div>
      <div className="c__window__content">{content}</div>
    </Card>
  );
};
