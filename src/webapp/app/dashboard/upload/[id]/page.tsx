'use server'

import { DocumentUpload } from "@/components/forms/file-upload"
import { ChangeList } from "@/components/process/change-list"
import { Editor } from "@/components/process/editor"
import { Reloader } from "@/components/process/reloader"
import { getWordingFileUrls, loadProcessDocuments } from "@/helper/pocketbase"
import { ArrowPathIcon, DocumentCheckIcon } from "@heroicons/react/24/outline"
import Link from "next/link"

const Upload = async ({ params }: any) => {
    params = await params
    const process = await loadProcessDocuments(params.id)
    const urls = await getWordingFileUrls(process)


    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <>
                <h2 className="text-2xl font-bold">Contracts</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                        <p className="text-sm font-bold">Uploaded Documents:</p>
                        {process.wordings.map((w: any, i: number) => (
                            <Link key={w} className="flex gap-2 items-center" href={urls[i]} target="_blank" rel="noopener noreferer">
                                <DocumentCheckIcon className="w-4 h-4" />
                                <span className="text-sm">{w}</span>
                            </Link>
                        ))}
                    </div>
                    <Reloader processId={params.id} />
                    {process.status == 'PROCESSING' &&
                        <>
                            <p className="text-sm flex items-center gap-2 font-bold"><ArrowPathIcon className='w-4 h-4 animate-spin' /> Processing Documents</p>
                            <p className="text-sm text-gray-700">Computes the YoY difference between the uploaded writings. Check back in a minute when we are done processing your contracts.</p>
                        </>
                    }
                </div>
                {process.status != 'PROCESSING' &&
                    <>
                        <h2 className="text-2xl font-bold">Changes</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm text-gray-700">The following changes were identified.</p>
                            <ul className="list-disc px-4">
                                {process.changes?.significant_changes.map((c: any, i: never) => (
                                    <li key={i} className="text-sm text-gray-800 p-2">
                                        {c}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <h2 className="text-2xl font-bold">Investigate</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm text-gray-700">Choose the suggestions for further investigation.</p>
                            <ChangeList process={process} />
                        </div>
                    </>
                }
                {process.significant_changes &&
                    <>
                        <h2 className="text-2xl font-bold">Edit the Report</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm">Here is a draft of the underwriting report.</p>

                            <Editor processId={params.id} initialValue={process.report_draft} />
                        </div>
                    </>

                }
            </>
        </div>
    )
}

export default Upload