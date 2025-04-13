'use server'
import { EventSource } from "eventsource"

import { ChangeList } from "@/components/process/change-list"
import { GenerateReport } from "@/components/process/generate-report"
import { Reloader } from "@/components/process/reloader"
import { getWordingFileUrls, loadProcessDocuments } from "@/helper/pocketbase"
import { ArrowPathIcon, DocumentCheckIcon } from "@heroicons/react/24/outline"
import Link from "next/link"

global.EventSource = EventSource

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
                {process.significant_changes && (!process.report || !process?.report['report'] ) &&
                    <>
                        <h2 className="text-2xl font-bold">Generate Report</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                            <p className="text-sm text-gray-700">Click generate to start the report generation task.</p>
                            <GenerateReport process={process} />
                        </div>
                    </>

                }
                {process.report &&
                    <>
                        <h2 className="text-2xl font-bold">Report Draft</h2>
                        <div className="bg-white p-4 rounded-sm flex flex-col gap-4">

                            {!process?.report['report'] &&
                                <p className="text-sm text-gray-700">Something went wrong while generating your report.</p>
                            }
                            
                            {process?.report['report'] &&
                                <>
                                    <p className="text-sm text-gray-700">The first draft for your report is ready</p>

                                    {process?.report['report']['quotation_line'] &&
                                        <>
                                            <h4 className="font-bold">Quotation Lines</h4>
                                            <p>{process?.report['report']['quotation_line']['suggestion_text']}</p>
                                        </>
                                    }

                                    {process?.report['report']['total_line'] &&
                                        <>
                                            <h4 className="font-bold">Total Line</h4>
                                            <pre>
                                                {JSON.stringify(process?.report['report']['total_line'], null, 2)}
                                            </pre>
                                        </>
                                    }

                                    {process?.report['report']['quotation_proposal'] &&
                                        <>
                                            <h4 className="font-bold">Quotation Proposal</h4>
                                            <pre>
                                                {JSON.stringify(process?.report['report']['quotation_proposal'], null, 2)}
                                            </pre>
                                        </>
                                    }

                                    {process?.report['report']['rationale'] &&
                                        <>
                                            <h4 className="font-bold">Rationale</h4>
                                            <p>{process?.report['report']['rationale']}</p>
                                        </>
                                    }

                                    {process?.report['report']['historical_losses'] &&
                                        <>
                                            <h4 className="font-bold">Historical Losses</h4>
                                            <p>{process?.report['report']['historical_losses']}</p>
                                        </>
                                    }

                                    {process?.report['report']['structure_key_changes'] &&
                                        <>
                                            <h4 className="font-bold">Key Changes</h4>
                                            <p>{process?.report['report']['structure_key_changes']}</p>
                                        </>
                                    }

                                    {process?.report['report']['key_findings'] &&
                                        <>
                                            <h4 className="font-bold">Key Findings</h4>
                                            <ul className="list-disc px-4">
                                                {process?.report['report']['key_findings'].length == 0 &&
                                                    <li>None</li>
                                                }
                                                {process?.report['report']['key_findings'].map((c: any, i: any) => (
                                                    <li key={i}>{c}</li>
                                                ))}
                                            </ul>
                                        </>
                                    }


                                    {process?.report['report']['investigation_points'] &&
                                        <>
                                            <h4 className="font-bold">Further Investigation</h4>
                                            <ul className="list-disc px-4">
                                                {process?.report['report']['investigation_points'].length == 0 &&
                                                    <li>None</li>
                                                }
                                                {process?.report['report']['investigation_points'].map((c: any, i: any) => (
                                                    <li key={i}>
                                                        <span className="font-bold">{c.question}: </span><br />
                                                        <span className="text-gray-700">{c.answer}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </>
                                    }

                                    {process?.report['report']['missing_information_summary'] &&
                                        <>
                                            <h4 className="font-bold">Missing Information</h4>
                                            <ul className="list-disc px-4">
                                                {process?.report['report']['missing_information_summary'].length == 0 &&
                                                    <li>None</li>
                                                }
                                                {process?.report['report']['missing_information_summary'].map((c: any, i: any) => (
                                                    <li key={i}>{c}</li>
                                                ))}
                                            </ul>
                                        </>
                                    }
                                </>

                            }


                        </div>
                    </>

                }
            </>
        </div>
    )
}

export default Upload