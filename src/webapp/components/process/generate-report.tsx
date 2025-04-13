'use client'

import { Button } from "../ui/button"

export const GenerateReport = ({process}: any) => {


    const generateReport = async () => {
        console.log({process})
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
    }


    return (
        <>
            <Button variant='main' onClick={() => generateReport()}>Generate Report</Button>
        </>
    )
}