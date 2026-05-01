import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalizedStatus = status.toLowerCase();
  
  if (normalizedStatus === 'completed' || normalizedStatus === 'success') {
    return <Badge className="bg-green-500 hover:bg-green-600">Success</Badge>;
  }
  
  if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
    return <Badge variant="destructive" className="bg-red-500 hover:bg-red-600">Failed</Badge>;
  }
  
  return <Badge variant="secondary" className="bg-amber-500 hover:bg-amber-600 text-white hover:text-white">Running</Badge>;
}
