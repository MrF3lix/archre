'use client'

import { useState } from "react"
import { Button } from "../ui/button"
import { ArrowPathIcon } from "@heroicons/react/24/outline"

export const GenerateReport = ({process}: any) => {
    const [isLoading, setIsLoading] = useState(false)


    const generateReport = async () => {
        console.log({process})
        setIsLoading(true)
        await fetch('/api/create-report-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                id: process.id,
                client: process.client,
                investigation_points: process.significant_changes,
                significant_changes_json: process.changes['significant_changes']
            }),
        })
        setIsLoading(false)
    }


    return (
        <>
            <Button variant='main' disabled={isLoading} onClick={() => generateReport()} className="flex items-center gap-1">
                {isLoading && <ArrowPathIcon className='w-4 h-4 animate-spin' />}
                Generate Report
            </Button>
        </>
    )
}