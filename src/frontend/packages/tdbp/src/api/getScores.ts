import dayjs from "dayjs";
import { useQuery } from "@tanstack/react-query";
import { AxiosInstance } from "axios";
import { apiAxios, useTokenInterceptor } from "@openfun/warren-core";
import { Action } from "./getSlidingWindow";

const DEFAULT_BASE_QUERY_KEY = "scoresCohort";

export type Scores = {
  actions: Array<Action>;
  scores: {
    [id: string]: Array<number>;
  };
  total?: Array<number>;
  average?: Array<number>;
};

type ScoresQueryParams = {
  course_id: string;
  until: string;
  totals?: boolean;
  average?: boolean;
};

const getScore = async (
  client: AxiosInstance,
  queryParams: ScoresQueryParams,
): Promise<Scores> => {
  queryParams.until = dayjs(queryParams.until).format("YYYY-MM-DD");
  const response = await client.get(`tdbp/scores`, {
    params: queryParams,
  });
  return response?.data;
};

type UseScoresReturn = {
  data: Scores | undefined;
  isFetching: boolean;
};

export const useScore = (
  queryParams: ScoresQueryParams,
  enabled?: boolean,
): UseScoresReturn => {
  // Get the API client, set with the authorization headers and refresh mechanism
  const client = useTokenInterceptor(apiAxios);

  const queryResult = useQuery({
    queryKey: [DEFAULT_BASE_QUERY_KEY, queryParams],
    queryFn: () => getScore(client, queryParams),
    staleTime: Infinity,
    enabled,
  });

  const { isFetching, data } = queryResult;
  return {
    data,
    isFetching,
  };
};
