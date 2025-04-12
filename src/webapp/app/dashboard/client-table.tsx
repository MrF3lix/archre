'use client'

import { useAsync } from 'react-use'
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "./data-table"
import { Button } from "@/components/ui/button"
import { ArrowsUpDownIcon } from "@heroicons/react/24/outline"
import Link from "next/link"
import { getClients, Client } from "@/helper/pocketbase"

const columns: ColumnDef<Client>[] = [
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
        }
    },
    {
        accessorKey: "cedantName",
        header: ({ column }) => {
            return (
                <button
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    className="flex font-bold"
                >
                    <span>Cedant</span>
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
                <Link href={`/dashboard/client/${cell.row.original.id}`} className="underline">
                    View
                </Link>
            )
        },
    },
]



const ClientTable = () => {

    const state = useAsync(async () => {
        const clients = await getClients()
        return clients
    }, []);

    return (
        <>
            <h1 className="text-2xl font-bold">Clients</h1>
            <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                {!state.loading && state.value &&
                    <DataTable columns={columns} data={state.value} />
                }
            </div>
        </>
    )
}

export default ClientTable