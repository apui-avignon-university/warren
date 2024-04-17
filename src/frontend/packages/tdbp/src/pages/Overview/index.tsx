import React from "react";
import { Flexgrid } from "@openfun/warren-core";
import { Filters } from "../../components/Filters";
import { Window } from "../../components/Window";
import { Activites } from "../../components/Activities";
import { Radar } from "../../components/Radar";
import { StudentsComparison } from "../../components/StudentsComparison";
import { TdbpFiltersProvider } from "../../contexts";

/**
 * A React component responsible for rendering a dashboard overview of student activity
 * statistics.
 *
 * @returns {JSX.Element} The JSX for the students activity overview dashboard.
 */
export default () => {
  return (
    <div className="c__overview">
      <TdbpFiltersProvider>
        <Filters />
        <Window />
        <Flexgrid>
          <Activites />
          <StudentsComparison />
          <Radar />
        </Flexgrid>
      </TdbpFiltersProvider>
    </div>
  );
};
