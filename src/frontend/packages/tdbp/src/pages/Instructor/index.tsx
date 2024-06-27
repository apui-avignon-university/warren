import { Flexgrid, useJwtContext } from "@openfun/warren-core";
import { Filters } from "../../components/Filters";
import { Window } from "../../components/Window";
import { ActiveActions } from "../../components/ActiveActions";
import { Radar } from "../../components/Radar";
import { StudentsComparison } from "../../components/StudentsComparison";
import { TdbpFiltersProvider } from "../../contexts";
import { Actions, Cohort } from "../../components";

/**
 * A React component responsible for rendering a dashboard overview of student activity
 * statistics.
 *
 * @returns {JSX.Element} The JSX for the students activity overview dashboard.
 */
export default () => {
  const { decodedJwt } = useJwtContext();

  if (!decodedJwt.course_id) {
    throw new Error("Unable to find `course_id` in the LTI context.");
  }

  return (
    <div className="c__overview">
      <TdbpFiltersProvider>
        <Filters />
        <Flexgrid>
          <Window course_id={decodedJwt.course_id} />
          <Actions course_id={decodedJwt.course_id} />
          <Cohort course_id={decodedJwt.course_id} />
        </Flexgrid>
        <Flexgrid>
          <ActiveActions
            course_id={decodedJwt.course_id}
            enumType="Resource"
            title="Taux de consultation des ressources"
          />
          <ActiveActions
            course_id={decodedJwt.course_id}
            enumType="Activity"
            title="Taux d'activation des activités"
          />
          <Radar course_id={decodedJwt.course_id} />
          <StudentsComparison course_id={decodedJwt.course_id} />
        </Flexgrid>
      </TdbpFiltersProvider>
    </div>
  );
};
