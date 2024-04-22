import React from "react";
import {
  DatePicker,
  Button,
  CunninghamProvider,
} from "@openfun/cunningham-react";
import dayjs from "dayjs";
import { queryClient } from "@openfun/warren-core";
import { useTdbpFilters } from "../../hooks/useTdbpFilters";
import { formatDate, getDefaultDate } from "../../utils";

/**
 * A React functional component for filtering on a end date.
 *
 * This component provides user interface elements to select the end date from a calendar,
 * and to trigger a data refresh.
 *
 * @returns {JSX.Element} The JSX for the Filters component.
 */
export const Filters = () => {
  const { until, setUntil } = useTdbpFilters();

  return (
    <div className="c__filters">
      <CunninghamProvider currentLocale="fr-FR">
        <DatePicker
          className="c__filters__date-picker"
          label="Date de fin"
          maxValue={dayjs().endOf("day").format()}
          value={until}
          onChange={(value) =>
            setUntil(value ? formatDate(value) : getDefaultDate())
          }
        />
        <Button
          className="c__filters__refresh"
          aria-label="Refresh dashboard"
          color="tertiary"
          icon={<span className="material-icons">cached</span>}
          onClick={() => queryClient.refetchQueries({ type: "active" })}
        />
      </CunninghamProvider>
    </div>
  );
};
