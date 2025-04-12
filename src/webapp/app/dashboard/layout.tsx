'use client'

import { Button } from "@/components/ui/button";
import { logout } from "../auth/logout";
import Image from "next/image";
import useCookie from "@/lib/use-cookies";
import { getAvatarUrl } from "@/lib/pocketbase";
import { useEffect, useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ArrowLeftEndOnRectangleIcon } from "@heroicons/react/24/outline";

const DashboardLayout = ({ children }: Readonly<{ children: React.ReactNode }>) => {

  const [auth, setAuth] = useCookie('pb_auth', null)
  const [avatarUrl, setAvatarUrl] = useState<string>()

  const loadAvatar = async () => {
    const url = await getAvatarUrl(auth.model)
    setAvatarUrl(url)

  }

  useEffect(() => {
    loadAvatar()
  }, [auth])

  return (
    <>
      <nav className="bg-white w-full">
        <div className="w-full max-w-[1200px] mx-auto flex px-4">
          <div className="px-4 py-2 flex flex-1 gap-4 justify-between items-center">
            <div className="flex gap-4 items-center">
              <Image src="/logo.png" width={50} height={50} alt="Logo" priority={true} />
              <p className="text-xl">Underwriter Assistant</p>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger>
                <Avatar>
                  <AvatarImage src={avatarUrl} />
                  <AvatarFallback>FS</AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>{auth?.model?.name}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="cursor-pointer">
                  <ArrowLeftEndOnRectangleIcon width={10} />
                  <span>Logout</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </nav>
      <main className="w-full max-w-[1200px] mx-auto flex flex-col min-h-screen">
        <div className="p-8 flex flex-1 flex-col gap-4 justify-center items-center">
          {children}
        </div>
      </main >
    </>
  )
}

export default DashboardLayout