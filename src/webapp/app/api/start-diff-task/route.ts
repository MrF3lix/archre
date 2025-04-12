import { setProcessStatus } from '@/helper/pocketbase'
import { NextRequest } from 'next/server'

// curl -X GET reporter:8000/api/v1/contractdiff -H "Content-Type: application/json" -d '{"contract_old": "pbc_391014268/v42lwgjddn1sh44/2024_wording_aqd8c92b9q.md", "contract_new": "pbc_391014268/v42lwgjddn1sh44/2025_wording_85i1nmycrj.md" }'

export async function POST(req: NextRequest) {
  try {

    const payload = await req.json()
    await setProcessStatus(payload.id, 'PROCESSING')

    const collection = 'pbc_391014268'
    const processId = payload.id

    const response = await fetch(`${process.env.REPORTER_URL}/contractdiff `, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "contract_old": `${collection}/${processId}/${payload.files[0].split('/').at(-1)}`,
        "contract_new": `${collection}/${processId}/${payload.files[1].split('/').at(-1)}` 
      }),
    })

    const data = await response.json()

    await setProcessStatus(payload.id, 'Ready')
    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error) {
    console.error('Error forwarding request:', error)
    return new Response(
      JSON.stringify({ error: 'Failed to forward request' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
