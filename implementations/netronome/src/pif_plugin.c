#include <pif_plugin.h>
#include <nfp.h>
#include <mem_atomic.h>

#define SEM_COUNT 30004
__declspec(imem export aligned(64)) int global_semaphores[SEM_COUNT];

void semaphore_down(volatile __declspec(mem addr40) void * addr) {
	/* semaphore "DOWN" = claim = wait */
	unsigned int addr_hi, addr_lo;
	__declspec(read_write_reg) int xfer;
	SIGNAL_PAIR my_signal_pair;
	addr_hi = ((unsigned long long int)addr >> 8) & 0xff000000;
	addr_lo = (unsigned long long int)addr & 0xffffffff;
	do {
		xfer = 1;
		__asm {
            mem[test_subsat, xfer, addr_hi, <<8, addr_lo, 1],\
                sig_done[my_signal_pair];
            ctx_arb[my_signal_pair]
        }
	} while (xfer == 0);
}

void semaphore_up(volatile __declspec(mem addr40) void * addr) {
	/* semaphore "UP" = release = signal */
	unsigned int addr_hi, addr_lo;
	__declspec(read_write_reg) int xfer;
	addr_hi = ((unsigned long long int)addr >> 8) & 0xff000000;
	addr_lo = (unsigned long long int)addr & 0xffffffff;

    __asm {
        mem[incr, --, addr_hi, <<8, addr_lo, 1];
    }
}

void pif_plugin_init_master() {
	int i;
	for (i = 0; i < SEM_COUNT; i++) {
		semaphore_up(&global_semaphores[i]);
	}
}

void pif_plugin_init() { }

int pif_plugin_cep_index_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_down(&global_semaphores[10000]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_index_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_up(&global_semaphores[10000]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_distinct_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_down(&global_semaphores[10001]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_distinct_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_up(&global_semaphores[10001]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_old_distinct_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_down(&global_semaphores[10003]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_old_distinct_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_up(&global_semaphores[10003]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_variation_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_down(&global_semaphores[10002]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_variation_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
    semaphore_up(&global_semaphores[10002]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_cfb_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
	__lmem struct pif_header_ingress__myParams *ingress__myParams;
	ingress__myParams = (__lmem struct pif_header_ingress__myParams *) (headers + PIF_PARREP_ingress__myParams_OFF_LW);
    semaphore_down(&global_semaphores[ingress__myParams->index]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_cfb_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
	__lmem struct pif_header_ingress__myParams *ingress__myParams;
	ingress__myParams = (__lmem struct pif_header_ingress__myParams *) (headers + PIF_PARREP_ingress__myParams_OFF_LW);
    semaphore_up(&global_semaphores[ingress__myParams->index]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_position_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
	__lmem struct pif_header_ingress__myParams *ingress__myParams;
	ingress__myParams = (__lmem struct pif_header_ingress__myParams *) (headers + PIF_PARREP_ingress__myParams_OFF_LW);
    semaphore_down(&global_semaphores[ingress__myParams->fingerprint]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_position_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
	__lmem struct pif_header_ingress__myParams *ingress__myParams;
	ingress__myParams = (__lmem struct pif_header_ingress__myParams *) (headers + PIF_PARREP_ingress__myParams_OFF_LW);
    semaphore_up(&global_semaphores[ingress__myParams->fingerprint]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_rm_position_lock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
	__lmem struct pif_header_ingress__myParams *ingress__myParams;
	ingress__myParams = (__lmem struct pif_header_ingress__myParams *) (headers + PIF_PARREP_ingress__myParams_OFF_LW);
    semaphore_down(&global_semaphores[ingress__myParams->rm_fingerprint]);
    return PIF_PLUGIN_RETURN_FORWARD;
}

int pif_plugin_cep_rm_position_unlock(EXTRACTED_HEADERS_T *headers, MATCH_DATA_T *data) {
	__lmem struct pif_header_ingress__myParams *ingress__myParams;
	ingress__myParams = (__lmem struct pif_header_ingress__myParams *) (headers + PIF_PARREP_ingress__myParams_OFF_LW);
    semaphore_up(&global_semaphores[ingress__myParams->rm_fingerprint]);
    return PIF_PLUGIN_RETURN_FORWARD;
}