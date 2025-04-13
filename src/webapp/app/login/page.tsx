'use client'

import PocketBase from 'pocketbase'
import Cookies from 'js-cookie'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)

const Login = () => {
    const router = useRouter()
    const [otpId, setOtpId] = useState<any>()
    const [email, setEmail] = useState<any>('')
    const [otp, setOtp] = useState<any>('')

    const otpRequest = async () => {
        const result = await pb.collection('users').requestOTP(email)
        setOtpId(result.otpId)
    }

    const otpLogin = async () => {
        const { token, record: model } = await pb.collection('users').authWithOTP(otpId, otp);

        const cookie = JSON.stringify({ token, model });
        Cookies.set('pb_auth', cookie)

        router.push('/dashboard');
    }

    const login = async (provider: string) => {
        const pb = new PocketBase(process.env.NEXT_PUBLIC_POCKETBASE_URL)
        const { token, record: model } = await pb
            .collection('users')
            .authWithOAuth2({
                provider: provider
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
                    <div className='flex flex-col w-full gap-1'>
                        <label className='text-xs'>Login with your E-Mail</label>
                        <input className='p-2 border rounded-sm border-gray-300 text-sm' type='email' placeholder='E-Mail Address' value={email} onChange={e => setEmail(e.target.value)} />
                    </div>
                    {!otpId &&
                        <Button variant="main" className='w-full' onClick={() => otpRequest()}>Request OTP</Button>
                    }
                    {otpId &&
                        <>
                            <div className='flex flex-col w-full gap-1'>
                                <label className='text-xs'>Your Code</label>
                                <input className='p-2 border rounded-sm border-gray-300 text-sm' type='text' placeholder='One Time Password' value={otp} onChange={e => setOtp(e.target.value)} />
                            </div>
                            <Button variant="main" className='w-full' onClick={() => otpLogin()}>Sign In</Button>
                        </>
                    }
                    <hr className="h-px bg-gray-200 border-0 w-full" />
                    <p className="text-xs text-gray-800">Or sign in with an existing Account</p>
                    <Button onClick={() => login('github')} className='w-full'>Login with Gitub</Button>
                    <Button onClick={() => login('oidc')} className='w-full'>Login with OIDC</Button>

                </div>
            </div>
        </main>
    )
}
export default Login