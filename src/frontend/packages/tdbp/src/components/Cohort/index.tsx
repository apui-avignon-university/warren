import React from "react";

import { Card } from "@openfun/warren-core";
import { useSlidingWindow } from "../../api/getSlidingWindow";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";

interface CohortProps {
  course_id: string;
}

/**
 * A React component for displaying the size of the dynamic cohort.
 *
 * @returns {JSX.Element} The JSX for the Cohort component.
 */
export const Cohort = ({ course_id }: CohortProps) => {
  const { until } = useTdbpFilters();
  const { slidingWindow } = useSlidingWindow({ course_id, until });

  const cohortLength = slidingWindow?.dynamic_cohort?.length || 0;
  const content = !slidingWindow?.dynamic_cohort
    ? "-"
    : `${cohortLength} ${cohortLength > 1 ? "élèves" : "élève"}`;

  return (
    <Card className="c__cohort">
      <div className="c__cohort__title">Cohorte dynamique</div>
      <div className="c__cohort__content">{content}</div>
    </Card>
  );
};
