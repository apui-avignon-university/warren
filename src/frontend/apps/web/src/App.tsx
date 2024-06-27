import React, { lazy } from "react";
import {
  AppContentLoader,
  parseDataContext,
  Routes,
  AppLayout,
  AppProvider,
} from "@openfun/warren-core";

const dataContext = parseDataContext(document);

const tdbpRoutes: Routes = {
  instructor: lazy(
    () => import("@apuiavignonuniversity/warren-tdbp/src/pages/Instructor"),
  ),
  student: lazy(
    () => import("@apuiavignonuniversity/warren-tdbp/src/pages/Student"),
  ),
};

const getTdbpRoute = (): React.LazyExoticComponent<() => JSX.Element> => {
  if (dataContext.is_instructor) {
    return tdbpRoutes.instructor;
  } else {
    return tdbpRoutes.student;
  }
};

const routes: Routes = {
  tdbp: getTdbpRoute(),
};

export const App = () => {
  return (
    <AppProvider>
      <AppLayout>
        <AppContentLoader dataContext={dataContext} routes={routes} />
      </AppLayout>
    </AppProvider>
  );
};
