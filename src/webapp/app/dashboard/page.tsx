import ClientTable from "./client-table"
import TermTable from "./term-table"



export default function Dashboard() {
    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <ClientTable />
            <TermTable />
        </div>
    )
}