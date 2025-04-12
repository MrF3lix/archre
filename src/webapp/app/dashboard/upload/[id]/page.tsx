'use server'

import { DocumentUpload } from "@/components/forms/file-upload"
import { ChangeList } from "@/components/process/change-list"
import { Checkbox } from "@/components/ui/checkbox"
import { getWordingFileUrls, loadProcessDocuments, subscribeToProcessStatusChange } from "@/helper/pocketbase"
import { ArrowPathIcon, CheckBadgeIcon, DocumentCheckIcon, XMarkIcon } from "@heroicons/react/24/outline"
import { CheckCircle, XCircle } from "lucide-react"
import { revalidatePath } from "next/cache"
import Link from "next/link"


const Upload = async ({ params }: any) => {
    params = await params
    const process = await loadProcessDocuments(params.id)
    const urls = await getWordingFileUrls(process)

    // subscribeToProcessStatusChange(params.id, (e: any) => {
    //     console.log('REVALIDATE')
    //     revalidatePath(`/dashboard/upload/${params.id}`)
    //     // if(e.record.status === 'READY') {
    //     //     revalidatePath(`/dashboard/upload/${params.id}`)
    //     // }
    // })

    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <>
                <h2 className="text-2xl font-bold">1. Contract Changes</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    {/* <p className="text-sm">
                        Upload two wordings to find the significant differences.
                    </p> */}
                    {/* <DocumentUpload /> */}
                    <div className="flex flex-col gap-2">
                        <p className="text-sm font-bold">Uploaded Documents:</p>
                        {process.wordings.map((w: any, i: number) => (
                            <Link key={w} className="flex gap-2 items-center" href={urls[i]} target="_blank" rel="noopener noreferer">
                                <DocumentCheckIcon className="w-4 h-4" />
                                <span className="text-sm">{w}</span>
                            </Link>
                        ))}
                    </div>
                    {process.status == 'PROCESSING' &&
                        <>
                            <p className="text-sm flex items-center gap-2 font-bold"><ArrowPathIcon className='w-4 h-4 animate-spin' /> Processing Documents</p>
                            <p className="text-sm">Computes the YoY difference between the uploaded writings. Check back in a minute when we are done processing your contracts.</p>
                        </>
                    }
                </div>
                {process.status != 'PROCESSING' &&
                    <>
                        <h2 className="text-2xl font-bold">2. Select Significant Changes</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm">Select the changes that you assume to be most significant.</p>
                            <ChangeList process={process} />
                        </div>
                    </>
                }
                {process.significant_changes &&
                    <>
                        <h2 className="text-2xl font-bold">3. Upload Additional Files</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm">Select files which incldue additional context.</p>
                            <DocumentUpload />
                        </div>
                        <h2 className="text-2xl font-bold">4. Upload Additional Files</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm">Select files which incldue additional context.</p>
                            <DocumentUpload />
                        </div>
                    </>
                }
            </>
        </div>
    )
}

export default Upload