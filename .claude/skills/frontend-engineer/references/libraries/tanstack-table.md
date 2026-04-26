---
library: tanstack table
package: "@tanstack/react-table"
context7_library_id: /websites/tanstack_table
synced_version: latest
project_version: latest
declared_range: latest
benchmark_score: 85.44
source_reputation: High
last_synced: 2026-03-21
coverage: useReactTable, column definitions, sorting, filtering, pagination, row selection, flexRender
---

# TanStack Table

Headless table/datagrid. Provides state + logic, you provide the markup.

## Basic Setup

```tsx
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  type ColumnDef,
} from '@tanstack/react-table'

type Student = { id: string; name: string; score: number }

const columns: ColumnDef<Student>[] = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'score', header: 'Score' },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) => <button onClick={() => deleteStudent(row.original.id)}>Delete</button>,
  },
]

function StudentTable({ data }: { data: Student[] }) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map((hg) => (
          <tr key={hg.id}>
            {hg.headers.map((h) => (
              <th key={h.id}>
                {flexRender(h.column.columnDef.header, h.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

## Sorting

```tsx
import { getSortedRowModel, type SortingState } from '@tanstack/react-table'

const [sorting, setSorting] = useState<SortingState>([])

const table = useReactTable({
  data,
  columns,
  state: { sorting },
  onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})

// In header cell
<th
  onClick={header.column.getToggleSortingHandler()}
  className={header.column.getCanSort() ? 'cursor-pointer' : ''}
>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {{ asc: ' ↑', desc: ' ↓' }[header.column.getIsSorted() as string] ?? null}
</th>
```

## Column Filtering

```tsx
import { getFilteredRowModel, type ColumnFiltersState } from '@tanstack/react-table'

const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])

const table = useReactTable({
  data,
  columns,
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})

// Filter input in column header
<input
  value={(header.column.getFilterValue() as string) ?? ''}
  onChange={(e) => header.column.setFilterValue(e.target.value)}
  placeholder="Filter..."
/>
```

## Pagination

```tsx
import { getPaginationRowModel, type PaginationState } from '@tanstack/react-table'

const [pagination, setPagination] = useState<PaginationState>({ pageIndex: 0, pageSize: 10 })

const table = useReactTable({
  data,
  columns,
  state: { pagination },
  onPaginationChange: setPagination,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})

// Pagination controls
<div>
  <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>Prev</button>
  <span>Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}</span>
  <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>Next</button>
</div>
```

## Row Selection

```tsx
import { type RowSelectionState } from '@tanstack/react-table'

const [rowSelection, setRowSelection] = useState<RowSelectionState>({})

const selectionColumn: ColumnDef<Student> = {
  id: 'select',
  header: ({ table }) => (
    <input type="checkbox"
      checked={table.getIsAllRowsSelected()}
      onChange={table.getToggleAllRowsSelectedHandler()}
    />
  ),
  cell: ({ row }) => (
    <input type="checkbox"
      checked={row.getIsSelected()}
      onChange={row.getToggleSelectedHandler()}
    />
  ),
}

const table = useReactTable({
  data,
  columns: [selectionColumn, ...columns],
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  getCoreRowModel: getCoreRowModel(),
})

// Get selected rows
const selectedRows = table.getSelectedRowModel().rows.map(r => r.original)
```

## All Features Combined

```tsx
const table = useReactTable({
  data,
  columns,
  filterFns: {},
  state: { columnFilters, sorting, pagination, rowSelection, globalFilter },
  onColumnFiltersChange: setColumnFilters,
  onSortingChange: setSorting,
  onPaginationChange: setPagination,
  onRowSelectionChange: setRowSelection,
  onGlobalFilterChange: setGlobalFilter,
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
})
```

## Column Definition Patterns

```tsx
const columns: ColumnDef<Row>[] = [
  // Accessor key (simple)
  { accessorKey: 'name', header: 'Name' },

  // Accessor function (computed)
  { accessorFn: (row) => `${row.first} ${row.last}`, id: 'fullName', header: 'Full Name' },

  // Custom cell renderer
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ getValue }) => <Badge>{getValue<string>()}</Badge>,
  },

  // Custom sort function
  {
    accessorKey: 'priority',
    sortingFn: (a, b) => ['low', 'med', 'high'].indexOf(a.original.priority)
                       - ['low', 'med', 'high'].indexOf(b.original.priority),
  },
]
```
