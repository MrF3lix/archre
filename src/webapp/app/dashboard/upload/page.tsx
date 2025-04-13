'use client'

import { DocumentUpload } from "@/components/forms/file-upload"
import { getWordingFileUrls, loadProcessDocuments, setProcessStatus, subscribeToProcessStatusChange } from "@/helper/pocketbase"
import { redirect } from "next/navigation"

const Upload = () => {

    const setProcess = async (id: any) => {
        const process = await loadProcessDocuments(id)
        const urls = await getWordingFileUrls(process)
        fetch('/api/start-diff-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: id, files: urls }),
        })
        redirect(`/dashboard/upload/${id}`)
    }

    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <>
                <h2 className="text-2xl font-bold">Upload Contracts</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    <p className="text-sm">
                        Upload two wordings to find the significant differences.
                    </p>
                    <DocumentUpload processId={undefined} setProcessId={setProcess} />
                </div>
            </>
        </div>
    )
}

export default Upload