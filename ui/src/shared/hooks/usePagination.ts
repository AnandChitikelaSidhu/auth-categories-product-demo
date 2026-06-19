import { useCallback, useState } from "react";
import { DEFAULT_PAGE_SIZE, type PageSizeOption } from "@/shared/constants/pagination";

export function usePagination(initialPageSize: number = DEFAULT_PAGE_SIZE) {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSizeState] = useState(initialPageSize);

  const setPageSize = useCallback((size: PageSizeOption | number) => {
    setPageSizeState(size);
    setPage(1);
  }, []);

  const resetPage = useCallback(() => setPage(1), []);

  return { page, pageSize, setPage, setPageSize, resetPage };
}
