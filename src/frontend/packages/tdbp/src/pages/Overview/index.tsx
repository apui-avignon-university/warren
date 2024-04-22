import { Flexgrid, useLTIContext } from "@openfun/warren-core";
import { Filters } from "../../components/Filters";
import { Window } from "../../components/Window";
import { Activities } from "../../components/Activities";
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
  const { appData } = useLTIContext();

  if (!appData.course_id) {
    throw new Error("Unable to find `course_id` in the LTI context.");
  }

  return (
    <div className="c__overview">
      <TdbpFiltersProvider>
        <Filters />
        <Window course_id={appData.course_id} />
        <Flexgrid>
          <Activities course_id={appData.course_id} />
          <StudentsComparison course_id={appData.course_id} />
          <Radar course_id={appData.course_id} />
        </Flexgrid>
      </TdbpFiltersProvider>
    </div>
  );
};
