import React from "react";

import dayjs from "dayjs";
import { Card } from "@openfun/warren-core";
import { useSlidingWindow } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";

export const Window: React.FC = () => {
  const { until } = useTdbpFilters();

  const courseId = "wip";

  const { slidingWindow } = useSlidingWindow({ courseId, until });

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
