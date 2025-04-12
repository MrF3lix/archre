'use client'

import { Button } from "@/components/ui/button"
import { redirect } from "next/navigation"

const AddSubmissionButton = () => {
    return (
        <div className="flex justify-end">
            <Button variant="main" onClick={() => redirect('/dashboard/upload')}>Add Submission</Button>
        </div>
    )
}

export default AddSubmissionButton