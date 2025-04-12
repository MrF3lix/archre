'use client'

import { useAsync } from 'react-use'
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "./data-table"
import { ArrowPathIcon, ArrowsUpDownIcon } from "@heroicons/react/24/outline"
import Link from "next/link"
import { getProcesses, Process } from "@/helper/pocketbase"
import { Badge } from '@/components/ui/badge'

const mapStatus = (status: string) => {
    switch (status) {
        case 'DONE':
            return 'GREEN'
        case 'PROCESSING':
            return 'BLUE'
        case 'READY':
            return 'YELLOW'
    }
}

const columns: ColumnDef<Process>[] = [
    {
        accessorKey: "id",
        header: ({ column }) => {
            return (
                <button
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    className="flex font-bold"
                >
                    <span>Id</span>
                    <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
                </button>
            )
        }
    },
    {
        accessorKey: "status",
        header: ({ column }) => {
            return (
                <button
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    className="flex font-bold"
                >
                    <span>Status</span>
                    <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
                </button>
            )
        },
        cell: ({ row }) => {
            const value: string = row.getValue("status")

            return (
                <Badge variant={mapStatus(value)}>
                    {value == 'PROCESSING' && <ArrowPathIcon className='w-4 h-4 animate-spin' />}
                    {value}
                </Badge>
            )
        },
    },
    {
        accessorKey: "created",
        header: ({ column }) => {
            return (
                <button
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    className="flex font-bold"
                >
                    <span>Created</span>
                    <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
                </button>
            )
        }
    },
    {
        accessorKey: "action",
        header: "",
        cell: ({ cell }) => {
            return (
                <Link href={`/dashboard/upload/${cell.row.original.id}`} className="underline">
                    View
                </Link>
            )
        },
    },
]



const ProcessTable = () => {

    const state = useAsync(async () => {
        const clients = await getProcesses()
        return clients
    }, []);

    return (
        <>
            <h1 className="text-2xl font-bold">Processes</h1>
            <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                {!state.loading && state.value &&
                    <DataTable columns={columns} data={state.value} />
                }
            </div>
        </>
    )
}

export default ProcessTable