'use client'

import clsx from "clsx"
import { CheckCircle, XCircle } from "lucide-react"
import { useEffect, useState } from "react"
import { Button } from "../ui/button"
import { saveIrrelevantChanges, saveSignificantChange } from "@/helper/pocketbase"
import { useRouter } from "next/navigation"

export const ChangeList = ({ process }: any) => {
    const router = useRouter()
    const [isLoading, setIsLoading] = useState(true)
    const [irrelevantItems, setIrrelevantItems] = useState([])
    const [relevantItems, setRelevantItems] = useState([])

    useEffect(() => {
        if(!process.significant_changes) {
            setIsLoading(false)
            return
        }

        setIrrelevantItems(process.irrelevant_changes)
        setRelevantItems(process.significant_changes.filter((s: any) => s.investigate_further === true).map((s: any) => s.id))

        setIsLoading(false)

    }, [process])


    const toggleRelevant = (id: never) => {
        if (relevantItems.includes(id)) {
            setRelevantItems([...relevantItems.filter(r => r !== id)])
        } else {
            setRelevantItems([...relevantItems, id])
            setIrrelevantItems([...irrelevantItems.filter(r => r !== id)])
        }
    }

    const toggleIrrelevant = (id: never) => {
        if (irrelevantItems.includes(id)) {
            setIrrelevantItems([...irrelevantItems.filter(r => r !== id)])
        } else {
            setIrrelevantItems([...irrelevantItems, id])
            setRelevantItems([...relevantItems.filter(r => r !== id)])
        }
    }

    const save = async (e: any) => {
        e.preventDefault()
        const data = new FormData(e.currentTarget)
        const significant_changes = process.changes?.suggestions_for_investigation.map((c: any, i: never) => {
            if (irrelevantItems.includes(i)) {
                return undefined
            }
            if (relevantItems.includes(i)) {
                return {
                    id: i,
                    change: c,
                    investigate_further: true,
                    expert_note: data.get(`expert_${i}`) || ''
                }
            }
            return {
                id: i,
                change: c,
                investigate: false,
            }

        })

        await saveIrrelevantChanges(process.id, irrelevantItems)
        await saveSignificantChange(process.id, significant_changes.filter((s: any) => s != null))

        router.refresh()
    }

    return (
        <form onSubmit={save} className="flex flex-col gap-4">
            <div className="grid grid-flow-row-dense grid-cols-3 gap-4">
                {!isLoading && process.changes?.suggestions_for_investigation.map((c: any, i: never) => (
                    <div key={i}
                        className={clsx(
                            "p-2 flex flex-col gap-2 border  rounded-sm justify-between",
                            irrelevantItems.includes(i) ? 'text-gray-300 border-gray-100' : 'border-gray-300'
                        )}
                    >
                        <span className="text-sm">{c}</span>
                        <div className="flex gap-4">
                            <div
                                onClick={() => toggleRelevant(i)}
                                className={clsx(
                                    "text-xs text-green-600 flex items-center gap-1 cursor-pointer py-1 px-2 rounded-full",
                                    relevantItems.includes(i) ? 'bg-green-500 text-white' : ''
                                )}>
                                Investigate Further <CheckCircle className="w-4 h-4" />
                            </div>
                            <div
                                onClick={() => toggleIrrelevant(i)}
                                className={clsx(
                                    "text-xs text-red-600 flex items-center gap-1 cursor-pointer py-1 px-2 rounded-full",
                                    irrelevantItems.includes(i) ? 'bg-red-500 text-white' : ''
                                )}>
                                Not Relevant <XCircle className="w-4 h-4" />
                            </div>
                        </div>
                        {relevantItems.includes(i) &&
                            <input
                                name={`expert_${i}`}
                                id={`expert_${i}`}
                                type="text"
                                defaultValue={process?.significant_changes?.find((s: any) => s.id == i)?.expert_note}
                                placeholder="Add your Expert Insights into why this is relevant"
                                className="p-2 text-xs border border-gray-300 rounded-sm"
                            />
                        }
                    </div>
                ))}
            </div>
            <div className="flex justify-end">
                <Button variant="main" type="submit">Save Significant Changes</Button>
            </div>
        </form>
    )
}