'use client'

import PocketBase from 'pocketbase'
import Cookies from 'js-cookie'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { Button } from '@/components/ui/button'

const Login = () => {
    const router = useRouter()

    const login = async () => {
        const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)
        const { token, record: model } = await pb
            .collection('users')
            .authWithOAuth2({
                provider: 'github'
            })

        const cookie = JSON.stringify({ token, model });
        Cookies.set('pb_auth', cookie)

        router.push('/dashboard');
    }

    return (
        <main className="w-full max-w-[1200px] mx-auto flex flex-col min-h-screen">
            <div className="p-4 flex flex-1 flex-col gap-4 justify-center items-center">
                <div className='bg-white w-96 p-4 rounded-sm border-1 border-gray-300 flex flex-col gap-4 items-center'>
                    <Image src="/logo.png" width={100} height={100} alt="Logo" priority={true} />
                    <h1 className="text-2xl leading-tight tracking-tight text-gray-900">Flooq Underwriter</h1>
                    <hr className="h-px bg-gray-200 border-0 dark:bg-gray-700 w-full" />
                    <p className="text-xs text-gray-800">Sign in or create an account using one of the providers.</p>
                    <Button variant="main" onClick={login} className='w-full'>Login with Gitub</Button>
                    <Button onClick={login} className='w-full'>Login with Microsoft</Button>
                    <Button onClick={login} className='w-full'>Login with Google</Button>

                </div>
            </div>
        </main>
    )
}
export default Login