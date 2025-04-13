'use client'

import { useState } from "react"
import MDEditor from '@uiw/react-md-editor'
import { Button } from "../ui/button"
import { saveReport } from "@/helper/pocketbase"

export const Editor = ({ processId, initialValue }: any) => {
    const [value, setValue] = useState(initialValue)

    return (
        <div className="container flex flex-col gap-4" data-color-mode="light">
            <div className="wmde-markdown-var"> </div>
            <MDEditor
                value={value}
                preview="edit"
                onChange={setValue}
            />

            <Button variant="main" className="self-end" onClick={() => saveReport(processId, value)}>Save Report</Button>
        </div>
    )
}