import dayjs, { Dayjs } from "dayjs";
import utc from "dayjs/plugin/utc";
import { formatDate } from "./formatDate";

dayjs.extend(utc);

export const getDefaultDate = (): string => {
  return formatDate(dayjs());
};
