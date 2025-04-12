'use client'

import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "./data-table"
import { ArrowsUpDownIcon } from "@heroicons/react/24/outline"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { useAsync } from "react-use"
import { getTerms, Terms } from "@/helper/pocketbase"

const mapStatus = (status: string) => {
    switch(status) {
        case 'Approved':
            return 'GREEN'
        case 'In Progress':
            return 'YELLOW'
        case 'Declined':
            return 'RED'
        case 'Todo':
            return 'BLUE'
    }
}

const columns: ColumnDef<Terms>[] = [
    {
        accessorKey: "year",
        header: ({ column }) => {
          return (
            <button
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                className="flex font-bold"
            >
                <span>Year</span>
                <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
            </button>
          )
        },
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
            <Badge variant={mapStatus(value)}>{value}</Badge>
          )
        },
    },
    {
        accessorKey: "country",
        header: ({ column }) => {
          return (
            <button
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                className="flex font-bold"
            >
                <span>Country</span>
                <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
            </button>
          )
        },
    },
    {
        accessorKey: "brokerName",
        header: "Broker",
    },
    {
        accessorKey: "cedant.name",
        header: "Cedant",
    },
    {
        accessorKey: "inceptionDate",
        header: ({ column }) => {
          return (
            <button
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                className="flex font-bold"
            >
                <span>Inception</span>
                <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
            </button>
          )
        },
    },
    {
        accessorKey: "expirationDate",
        header: ({ column }) => {
          return (
            <button
                onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                className="flex font-bold"
            >
                <span>Expiration</span>
                <ArrowsUpDownIcon className="ml-2 h-4 w-4" />
            </button>
          )
        },
    },
    {
        accessorKey: "action",
        header: "",
        cell: ({ cell }) => {
          return (
            <Link href={`/dashboard/contract/${cell.row.original.id}`} className="underline">
            View
            </Link>
          )
        },
    },
]


const TermTable = () => {

    const state = useAsync(async () => {
        const terms = await getTerms()
        return terms
    }, []);

    return (
        <>
        <h1 className="text-2xl font-bold">Terms</h1>
        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
            {!state.loading && state.value &&
                <DataTable columns={columns} data={state.value} />
            }
        </div>
        </>
    )
}

export default TermTable