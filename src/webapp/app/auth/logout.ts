'use server'
import PocketBase from 'pocketbase'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export const logout = async () => {
    const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)
    pb.authStore.clear()

    const cookieStore = await cookies()
    cookieStore.delete('pb_auth')
    redirect('/')
}