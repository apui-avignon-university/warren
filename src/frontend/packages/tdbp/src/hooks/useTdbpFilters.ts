import { useContext } from "react";
import { TdbpFiltersContext, TdbpFiltersContextType } from "../contexts/tdbpFiltersContext";

export const useTdbpFilters = (): TdbpFiltersContextType => {
  const value = useContext(TdbpFiltersContext);
  if (!value) {
    throw new Error(`Missing wrapping Provider for Store TdbpFiltersContextType`);
  }
  return value;
};
