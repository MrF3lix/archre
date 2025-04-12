'use server'

import { getClient } from "@/helper/pocketbase"

const Contract = async ({ params }: any) => {

    const client = await getClient(params.id)

    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <h1 className="text-2xl font-bold">Overview</h1>
            <div className="bg-white p-4 rounded-sm flex flex-col gap-4">
                <div className="px-4 sm:px-0">
                    <h3 className="text-base/7 font-semibold text-black">Client</h3>
                    <p className="mt-1 max-w-2xl text-sm/6 text-gray-800">Client details and contracts.</p>
                </div>
                <div className="mt-6 border-t border-white/10">
                    <dl className="divide-y divide-white/10">
                        <div className="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
                            <dt className="text-sm/6 font-medium text-black">Name</dt>
                            <dd className="mt-1 text-sm/6 text-gray-800 sm:col-span-2 sm:mt-0">{client.name}</dd>
                        </div>
                        <div className="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
                            <dt className="text-sm/6 font-medium text-black">Country</dt>
                            <dd className="mt-1 text-sm/6 text-gray-800 sm:col-span-2 sm:mt-0">{client.country}</dd>
                        </div>
                    </dl>
                </div>
            </div>
        </div>
    )
}

export default Contract