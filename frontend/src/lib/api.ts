import { Link } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getLinks(): Promise<Link[]> {
  const response = await fetch(`${API_URL}/links/`);
  if (!response.ok) {
    throw new Error("Failed to fetch links");
  }
  return response.json();
}

export async function deleteLink(linkId: number): Promise<void> {
  const response = await fetch(`${API_URL}/links/${linkId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete link");
  }
}
