import ClientTable from "./client-table"
import TermTable from "./term-table"
import AddSubmissionButton from "./add-button"
import ProcessTable from "./process-table"

export default function Dashboard() { 
    return (
        <div className="w-full flex-1 flex flex-col gap-4">
            <AddSubmissionButton />
            <ProcessTable />
            <ClientTable />
            <TermTable />
        </div>
    )
}