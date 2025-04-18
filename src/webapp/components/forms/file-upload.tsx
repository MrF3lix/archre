'use client'

import { setProcessStatus, uploadWordings } from "@/helper/pocketbase"
import { DocumentPlusIcon } from "@heroicons/react/24/outline"
import clsx from "clsx"
import { useRouter } from "next/navigation"
import { useState } from "react"


export const DocumentUpload = ({ processId, setProcessId, client }: any) => {
    const router = useRouter()
    const [isLoading, setIsLoading] = useState(false)
    const [isDragActive, setIsDragActive] = useState(false)

    const uploadFile = async (files: any) => {
        setIsLoading(true)
        const id = await uploadWordings(processId, client, files)

        await setProcessStatus(id, 'PROCESSING')
        if (!processId) {
            setProcessId(id)
        }
        setIsLoading(false)
        router.refresh()
    }

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        setIsDragActive(false)
        uploadFile(e.dataTransfer.files)
    }

    return (
        <div
            onDragEnter={() => setIsDragActive(true)}
            onDragLeave={() => setIsDragActive(false)}
            onDragOver={e => e.preventDefault()}
            onDrop={handleDrop}
            className={clsx(
                "flex flex-col gap-2 items-center justify-center border-dotted border-2 border-gray-300 text-gray-600 w-full p-8 rounded-md",
                isDragActive ? 'border-blue-500 text-blue-500 cursor-copy' : '',
                isLoading ? 'bg-gray-100' : ''
            )}
        >
            <DocumentPlusIcon className="w-8 h-8" />
            <span className="text-sm">Drop the wordings</span>
            
        </div>
    )
}
