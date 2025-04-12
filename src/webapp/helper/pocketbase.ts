import PocketBase from 'pocketbase'
import dayjs from 'dayjs'

const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)

export const getAvatarUrl = async (model: any) => {

    return pb.files.getURL(model, model.avatar);
}

export const getClient = async(id: string) => {
    const model = await pb.collection('clients').getOne(id)
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


export const startProcess = async (formData: any) => {
    const createdRecord = await pb.collection('process').create({
        wording_previous_year: formData.wording_prev,
        wording_next_year: formData.wording_next
    })

    console.log(createdRecord)
}