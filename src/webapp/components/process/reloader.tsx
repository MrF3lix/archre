'use client'

import { subscribeToProcessStatusChange } from "@/helper/pocketbase"
import { useRouter } from "next/navigation"

export const Reloader = ({ processId }: any) => {
    const router = useRouter()

    subscribeToProcessStatusChange(processId, (e: any) => {
        router.refresh()
    })

    return (
        <></>
    )
}