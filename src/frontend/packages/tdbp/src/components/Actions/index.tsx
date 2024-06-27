import React from "react";

import { Card } from "@openfun/warren-core";
import { useSlidingWindow } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";

interface ActionsProps {
  course_id: string;
}

/**
 * A React component for displaying the number of active actions.
 *
 * @returns {JSX.Element} The JSX for the Cohort component.
 */
export const Actions = ({ course_id }: ActionsProps) => {
  const { until } = useTdbpFilters();
  const { slidingWindow } = useSlidingWindow({ course_id, until });

  const actionsCount = slidingWindow?.active_actions?.length || 0;
  const content = !slidingWindow?.active_actions
    ? "-"
    : `${actionsCount} ${actionsCount > 1 ? "actions" : "action"}`;

  return (
    <Card className="c__actions">
      <div className="c__actions__title">Actions actives</div>
      <div className="c__actions__content">{content}</div>
    </Card>
  );
};
