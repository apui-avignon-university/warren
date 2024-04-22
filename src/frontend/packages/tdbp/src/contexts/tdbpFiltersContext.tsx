import React, {
  createContext,
  Dispatch,
  SetStateAction,
  useMemo,
  useState,
} from "react";
import { getDefaultDate } from "../utils";

export interface TdbpFiltersContextType {
  until: string;
  setUntil: Dispatch<SetStateAction<string>>;
}

export const TdbpFiltersContext = createContext<TdbpFiltersContextType | null>(
  null,
);

export const TdbpFiltersProvider: React.FC<{ children: any }> = ({
  children,
}) => {
  const defaultDate = getDefaultDate();
  const [until, setUntil] = useState<string>(defaultDate);

  const value = useMemo(() => ({ until, setUntil }), [until]);

  return (
    <TdbpFiltersContext.Provider value={value}>
      {children}
    </TdbpFiltersContext.Provider>
  );
};

export default TdbpFiltersContext;
