"use client";
import { useContext } from "react";
import { WorkspaceContext } from "@/context/WorkspaceContext";

export const useWorkspace = () => useContext(WorkspaceContext);
