export interface SampleType {
    id: number;
    name: string;
    description?: string;
}

export type SampleResponse = {
    success: boolean;
    data: SampleType[];
};

export interface Config {
    apiUrl: string;
    timeout: number;
}