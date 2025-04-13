import { getClient, saveContractChanges, saveProcessReport, setProcessStatus } from '@/helper/pocketbase'
import { NextRequest } from 'next/server'


export async function POST(req: NextRequest) {
  try {

    const payload = await req.json()

    const client = await getClient(payload.client)

    console.log({
      "client": client.country,
      "investigation_points": payload.investigation_points,
      "significant_changes_json": payload.significant_changes_json
    })

    const response = await fetch(`${process.env.REPORTER_URL}/generate `, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "client": client.country,
        "investigation_points": payload.investigation_points.map((x: any) => `${x.change}, EXPERT NOTE: ${x.expert_note}`),
        "significant_changes_json": payload.significant_changes_json
      }),
    })

    const data = await response.json()

    console.log(JSON.stringify(data, null, 2))

    await saveProcessReport(payload.id, data)
    setProcessStatus(payload.id, 'Done')

    return new Response(JSON.stringify({}), {
      status: response.status
    })
  } catch (error) {
    console.error('Error forwarding request:', error)
    return new Response(
      JSON.stringify({ error: 'Failed to forward request' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
