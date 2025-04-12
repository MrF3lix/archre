'use client'

import { startProcess } from "@/helper/pocketbase"
import { DocumentPlusIcon } from "@heroicons/react/24/outline"
import clsx from "clsx"
import { useRouter } from "next/navigation"
import { useState } from "react"


export const DocumentUpload = () => {
  const router = useRouter()
  const [isDragActive, setIsDragActive] = useState(false)

  const uploadFile = async (files: any) => {
    await startProcess(files)
    console.log(files)
    // const supabase = createClientComponentClient()

    // const tasks = Array.from(files).map(async (file: any) => {
    //   return supabase
    //     .storage
    //     .from('documents')
    //     .upload(`${customerId}/${file.name}`, file)
    // })

    // await Promise.all(tasks)


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
        "flex flex-col gap-2 items-center justify-center border-dotted border-2 w-full p-8 rounded-md",
        isDragActive ? 'border-blue-500 text-blue-500 cursor-copy' : ''
      )}
    >
      <DocumentPlusIcon className="w-8 h-8" />
      Upload new File
    </div>
  )
}
