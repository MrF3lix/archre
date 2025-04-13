import PocketBase from 'pocketbase'
import dayjs from 'dayjs'

const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)

export const getAvatarUrl = async (model: any) => {
    return pb.files.getURL(model, model.avatar);
}

export const getWordingFileUrls = async (model: any) => {
    const tasks = Array.from(model.wordings).map(async (file: any) => {
        return pb.files.getURL(model, file);
    })

    return await Promise.all(tasks)
}

export const getClient = async (id: string) => {
    const model = await pb.collection('cedant').getOne(id)
    return model
}

export type Client = {
    id: string
    cedantName: string
    country: string
}

export const getClients = async (): Promise<Client[]> => {
    const models = await pb.collection('cedant').getFullList()

    return models.map(c => ({
        id: c.id,
        cedantName: c.name,
        country: c.country
    }))
}

export type Terms = {
    id: string
    year: string
    status: string
    country: string
    brokerName: string
    cedant: any
    inceptionDate: string,
    expirationDate: string,
    content: any
}

export const getTerms = async (): Promise<Terms[]> => {
    const models = await pb.collection('terms').getFullList({ expand: "cedant" })


    return models.map(c => ({
        id: c.id,
        year: c.year,
        status: c.status,
        country: c.expand?.cedant.country,
        brokerName: c.brokerName,
        cedant: c.expand?.cedant,
        inceptionDate: dayjs(c.inceptionDate).format('YYYY-MM-DD'),
        expirationDate: dayjs(c.expirationDate).format('YYYY-MM-DD'),
        content: c.content
    }))
}

export type Process = {
    id: string,
    cedant: string,
    status: string,
    created: string
}

export const getProcesses = async (): Promise<Process[]> => {
    const models = await pb.collection('process').getFullList({ expand: 'client' })
    return models.map(c => ({
        id: c.id,
        cedant: c.expand?.client?.name || '-',
        status: c.status,
        created: dayjs(c.created).format('YYYY-MM-DD HH:mm'),
    }))
}


export const uploadWordings = async (processId: any | undefined, client: any, files: any) => {
    const formData = new FormData()

    Array.from(files).map(async (file: any) => {
        formData.append('wordings', file)
    })
    formData.append('client', client)

    const process = await pb.collection('process').create(formData)
    return process.id
}

export const loadProcessDocuments = async (processId: string) => {
    const process = await pb.collection('process').getOne(processId, { expand: 'wordings' })
    return process
}

export const saveContractChanges = async (processId: string, changes: number) => {
    const process = await pb.collection('process').update(processId, { changes })
    return process

}
export const saveProcessReport = async (processId: string, report: number) => {
    const process = await pb.collection('process').update(processId, { report })
    return process

}
export const saveSignificantChange = async (processId: string, significant_changes: number) => {
    const process = await pb.collection('process').update(processId, { significant_changes })
    return process

}

export const saveIrrelevantChanges = async (processId: string, irrelevantItems: any) => {
    const process = await pb.collection('process').update(processId, { irrelevant_changes: irrelevantItems })
    return process
}

export const setProcessStatus = async (processId: string, status: any) => {
    const process = await pb.collection('process').update(processId, { status })
    return process
}


export const subscribeToProcessStatusChange = (processId: string, callback: any) => {
    try {
        const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)

        pb.collection('process').subscribe(processId, (e) => {
            callback(e)
        });
    } catch(e) {
        console.log(e)
        console.error({ processId })
    }
}

export const saveReport = async (processId: string, report: any) => {
    const process = await pb.collection('process').update(processId, { report_draft: report })
    return process

}