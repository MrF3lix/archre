'use client'

import { DocumentUpload } from "@/components/forms/file-upload"
import { getClients, getWordingFileUrls, loadProcessDocuments, setProcessStatus, subscribeToProcessStatusChange } from "@/helper/pocketbase"
import { redirect } from "next/navigation"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useAsync } from "react-use"
import { useState } from "react"

const Upload = () => {

    const clients = useAsync(getClients, [])
    const [client, setClient] = useState()

    const setProcess = async (id: any) => {
        const process = await loadProcessDocuments(id)
        const urls = await getWordingFileUrls(process)
        fetch('/api/start-diff-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: id, files: urls, client: client }),
        })
        redirect(`/dashboard/upload/${id}`)
    }

    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <>
                <h2 className="text-2xl font-bold">Select Client</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    <p className="text-sm text-gray-700">
                        Select a client for the underwriting
                    </p>
                    <Select onValueChange={(e: any) => setClient(e)}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select a Client" />
                        </SelectTrigger>
                        <SelectContent>
                            {!clients.loading && clients.value?.map((c: any) => (
                                <SelectItem key={c.id} value={c.id}>{c.cedantName} - {c.country}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
                {client &&
                    <>
                        <h2 className="text-2xl font-bold">Upload Contracts</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm text-gray-700">
                                Upload two wordings to find the significant differences.
                            </p>
                            <DocumentUpload processId={undefined} setProcessId={setProcess} client={client} />
                        </div>
                    </>
                }
            </>
        </div>
    )
}

export default Upload