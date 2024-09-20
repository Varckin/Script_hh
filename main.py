if __name__ == '__main__':
    while True:
        for id in resume_id_list:
            update_resume(id)
            time.sleep(5)

        # sleep 90 minutes
        log.info('going sleep...')
        time.sleep(90 * 60)