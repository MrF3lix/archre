'use client'

import { DocumentUpload } from "@/components/forms/file-upload"
import { Button } from "@/components/ui/button"
import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { startProcess } from "@/helper/pocketbase"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm, FormProvider, useFormContext } from "react-hook-form"
import { z } from "zod"


const Upload = () => {

    const form = useForm()

    const onSubmit = async (e: any) => {
        e.preventDefault()
        console.log(e.target)
        console.log("files:", e.target.files)
        // console.log(values)

        // const formData = new FormData()
        
        // formData.append('wording_prev', values.wording_prev)
        // formData.append('wording_next', values.wording_next)

        // startProcess(formData)
    }

    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <>
                <h2 className="text-2xl font-bold">1. Contract Changes</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    <p className="text-sm">
                        Upload two wordings to find the significant differences.
                    </p>
                    <DocumentUpload />
                </div>
                <h2 className="text-2xl font-bold">2. Select Significant Chagnes</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    <p className="text-sm">Select the changes that you assume to be most significant.</p>
                </div>
                <h2 className="text-2xl font-bold">3. Upload Additional Files</h2>
                <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                    <p className="text-sm">Select files which incldue additional context.</p>
                </div>
            </>
        </div>
    )
}

export default Upload